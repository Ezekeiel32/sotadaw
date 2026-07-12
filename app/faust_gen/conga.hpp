/* ------------------------------------------------------------
name: "conga"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Conga -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Conga_H__
#define  __Conga_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Conga
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

static float Conga_faustpower2_f(float value) {
	return value * value;
}

class Conga : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst0;
	float fConst3;
	float fConst5;
	float fConst7;
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec1[2];
	float fConst8;
	float fConst9;
	float fConst10;
	int iRec2[2];
	float fRec0[3];
	FAUSTFLOAT fHslider0;
	float fConst11;
	FAUSTFLOAT fHslider1;
	float fConst12;
	float fRec3[3];
	float fConst13;
	float fRec4[3];
	float fConst14;
	float fRec5[3];
	float fConst15;
	float fConst16;
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	
 public:
	Conga() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Conga -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "conga.dsp");
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
		m->declare("name", "conga");
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
		float fConst1 = std::tan(3769.9111f / fConst0);
		float fConst2 = Conga_faustpower2_f(fConst1);
		fConst3 = 2.0f * (1.0f - 1.0f / fConst2);
		float fConst4 = 1.0f / fConst1;
		fConst5 = (fConst4 + -1.4142135f) / fConst1 + 1.0f;
		float fConst6 = (fConst4 + 1.4142135f) / fConst1 + 1.0f;
		fConst7 = 1.0f / fConst6;
		fConst8 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 1.0f / std::max<float>(1.0f, 0.03f * fConst0);
		fConst11 = 1.0f / (fConst2 * fConst6);
		fConst12 = 6.5973444f / fConst0;
		fConst13 = 4.775221f / fConst0;
		fConst14 = 3.1415927f / fConst0;
		fConst15 = std::max<float>(1.0f, 0.0015f * fConst0);
		fConst16 = 1.0f / fConst15;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.35f);
		fHslider1 = FAUSTFLOAT(1.9e+02f);
		fHslider2 = FAUSTFLOAT(0.22f);
		fHslider3 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec2[l2] = 0;
		}
		for (int l3 = 0; l3 < 3; l3 = l3 + 1) {
			fRec0[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec3[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 3; l5 = l5 + 1) {
			fRec4[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec5[l6] = 0.0f;
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
	
	virtual Conga* clone() {
		return new Conga();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("conga");
		ui_interface->addHorizontalSlider("decay", &fHslider2, FAUSTFLOAT(0.22f), FAUSTFLOAT(0.05f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider1, FAUSTFLOAT(1.9e+02f), FAUSTFLOAT(6e+01f), FAUSTFLOAT(6e+02f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("tone", &fHslider0, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = fConst11 * float(fHslider0);
		float fSlow2 = float(fHslider1);
		float fSlow3 = std::tan(fConst12 * fSlow2);
		float fSlow4 = 2.0f * (1.0f - 1.0f / Conga_faustpower2_f(fSlow3));
		float fSlow5 = 1.0f / fSlow3;
		float fSlow6 = (fSlow5 + -0.04f) / fSlow3 + 1.0f;
		float fSlow7 = (fSlow5 + 0.04f) / fSlow3 + 1.0f;
		float fSlow8 = 1.0f / fSlow7;
		float fSlow9 = 0.25f / (fSlow3 * fSlow7);
		float fSlow10 = std::tan(fConst13 * fSlow2);
		float fSlow11 = 2.0f * (1.0f - 1.0f / Conga_faustpower2_f(fSlow10));
		float fSlow12 = 1.0f / fSlow10;
		float fSlow13 = (fSlow12 + -0.045454547f) / fSlow10 + 1.0f;
		float fSlow14 = (fSlow12 + 0.045454547f) / fSlow10 + 1.0f;
		float fSlow15 = 1.0f / fSlow14;
		float fSlow16 = 0.5f / (fSlow10 * fSlow14);
		float fSlow17 = std::tan(fConst14 * fSlow2);
		float fSlow18 = 2.0f * (1.0f - 1.0f / Conga_faustpower2_f(fSlow17));
		float fSlow19 = 1.0f / fSlow17;
		float fSlow20 = (fSlow19 + -0.055555556f) / fSlow17 + 1.0f;
		float fSlow21 = (fSlow19 + 0.055555556f) / fSlow17 + 1.0f;
		float fSlow22 = 1.0f / fSlow21;
		float fSlow23 = 1.0f / (fSlow17 * fSlow21);
		float fSlow24 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow25 = 1.1f * float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iRec1[0] = (iRec1[1] + (iRec1[1] > 0)) * (fSlow0 <= fVec0[1]) + (fSlow0 > fVec0[1]);
			float fTemp0 = float(iRec1[0]);
			iRec2[0] = 1103515245 * iRec2[1] + 12345;
			fRec0[0] = 4.656613e-10f * float(iRec2[0]) * std::max<float>(0.0f, std::min<float>(fConst9 * fTemp0, fConst10 * (fConst8 - fTemp0) + 1.0f)) - fConst7 * (fConst5 * fRec0[2] + fConst3 * fRec0[1]);
			float fTemp1 = fSlow0 - fVec0[1];
			float fTemp2 = fTemp1 * float(fTemp1 > 0.0f);
			fRec3[0] = fTemp2 - fSlow8 * (fSlow6 * fRec3[2] + fSlow4 * fRec3[1]);
			fRec4[0] = fTemp2 - fSlow15 * (fSlow13 * fRec4[2] + fSlow11 * fRec4[1]);
			fRec5[0] = fTemp2 - fSlow22 * (fSlow20 * fRec5[2] + fSlow18 * fRec5[1]);
			float fTemp3 = fSlow25 * std::max<float>(0.0f, std::min<float>(fConst16 * fTemp0, fSlow24 * (fConst15 - fTemp0) + 1.0f)) * (3.2f * (fSlow23 * (fRec5[0] - fRec5[2]) + fSlow16 * (fRec4[0] - fRec4[2]) + fSlow9 * (fRec3[0] - fRec3[2])) + fSlow1 * (fRec0[0] + fRec0[2] - 2.0f * fRec0[1]));
			output0[i0] = FAUSTFLOAT(fTemp3);
			output1[i0] = FAUSTFLOAT(fTemp3);
			fVec0[1] = fVec0[0];
			iRec1[1] = iRec1[0];
			iRec2[1] = iRec2[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fRec5[2] = fRec5[1];
			fRec5[1] = fRec5[0];
		}
	}

};

#endif
