/* ------------------------------------------------------------
name: "hat"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Hat -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Hat_H__
#define  __Hat_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Hat
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float Hat_faustpower2_f(float value) {
	return value * value;
}

class Hat : public dsp {
	
 private:
	
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fHslider1;
	float fConst3;
	FAUSTFLOAT fHslider2;
	float fConst6;
	float fConst8;
	float fConst10;
	float fConst11;
	float fConst13;
	int iRec4[2];
	float fRec3[3];
	float fConst14;
	float fRec2[3];
	float fConst15;
	float fRec1[3];
	FAUSTFLOAT fHslider3;
	
 public:
	Hat() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Hat -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "hat.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "hat");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst2 = 1.0f / fConst1;
		fConst3 = 3.1415927f / fConst0;
		float fConst4 = std::tan(25132.742f / fConst0);
		float fConst5 = Hat_faustpower2_f(fConst4);
		fConst6 = 2.0f * (1.0f - 1.0f / fConst5);
		float fConst7 = 1.0f / fConst4;
		fConst8 = (fConst7 + -0.76536685f) / fConst4 + 1.0f;
		float fConst9 = (fConst7 + 0.76536685f) / fConst4 + 1.0f;
		fConst10 = 1.0f / fConst9;
		fConst11 = (fConst7 + -1.847759f) / fConst4 + 1.0f;
		float fConst12 = (fConst7 + 1.847759f) / fConst4 + 1.0f;
		fConst13 = 1.0f / fConst12;
		fConst14 = 1.0f / (fConst5 * fConst12);
		fConst15 = 1.0f / (fConst5 * fConst9);
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.05f);
		fHslider1 = FAUSTFLOAT(1e+04f);
		fHslider2 = FAUSTFLOAT(2.0f);
		fHslider3 = FAUSTFLOAT(0.5f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec0[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec4[l2] = 0;
		}
		for (int l3 = 0; l3 < 3; l3 = l3 + 1) {
			fRec3[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 3; l5 = l5 + 1) {
			fRec1[l5] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual Hat* clone() {
		return new Hat();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("hat");
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(0.05f), FAUSTFLOAT(0.01f), FAUSTFLOAT(0.6f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("sizzle", &fHslider2, FAUSTFLOAT(2.0f), FAUSTFLOAT(0.5f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("tone", &fHslider1, FAUSTFLOAT(1e+04f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(1.6e+04f), FAUSTFLOAT(1e+01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow2 = std::tan(fConst3 * float(fHslider1));
		float fSlow3 = 2.0f * (1.0f - 1.0f / Hat_faustpower2_f(fSlow2));
		float fSlow4 = 1.0f / float(fHslider2);
		float fSlow5 = 1.0f / fSlow2;
		float fSlow6 = (fSlow5 - fSlow4) / fSlow2 + 1.0f;
		float fSlow7 = (fSlow4 + fSlow5) / fSlow2 + 1.0f;
		float fSlow8 = 1.0f / fSlow7;
		float fSlow9 = 0.882f * (float(fHslider3) / (fSlow2 * fSlow7));
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iRec0[0] = (iRec0[1] + (iRec0[1] > 0)) * (fSlow0 <= fVec0[1]) + (fSlow0 > fVec0[1]);
			float fTemp0 = float(iRec0[0]);
			iRec4[0] = 1103515245 * iRec4[1] + 12345;
			fRec3[0] = 4.656613e-10f * float(iRec4[0]) - fConst13 * (fConst11 * fRec3[2] + fConst6 * fRec3[1]);
			fRec2[0] = fConst14 * (fRec3[2] + (fRec3[0] - 2.0f * fRec3[1])) - fConst10 * (fConst8 * fRec2[2] + fConst6 * fRec2[1]);
			fRec1[0] = fConst15 * (fRec2[2] + (fRec2[0] - 2.0f * fRec2[1])) - fSlow8 * (fSlow6 * fRec1[2] + fSlow3 * fRec1[1]);
			float fTemp1 = fSlow9 * (fRec1[0] - fRec1[2]) * std::max<float>(0.0f, std::min<float>(fConst2 * fTemp0, fSlow1 * (fConst1 - fTemp0) + 1.0f));
			output0[i0] = FAUSTFLOAT(fTemp1);
			output1[i0] = FAUSTFLOAT(fTemp1);
			fVec0[1] = fVec0[0];
			iRec0[1] = iRec0[0];
			iRec4[1] = iRec4[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
		}
	}

};

#endif
