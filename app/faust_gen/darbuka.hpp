/* ------------------------------------------------------------
name: "darbuka"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Darbuka -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Darbuka_H__
#define  __Darbuka_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Darbuka
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

static float Darbuka_faustpower2_f(float value) {
	return value * value;
}

class Darbuka : public dsp {
	
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
	float fConst15;
	float fConst16;
	float fConst17;
	FAUSTFLOAT fHslider2;
	float fConst18;
	float fRec5[3];
	float fRec6[3];
	FAUSTFLOAT fHslider3;
	
 public:
	Darbuka() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Darbuka -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "darbuka.dsp");
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
		m->declare("name", "darbuka");
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
		float fConst1 = std::tan(7853.9814f / fConst0);
		float fConst2 = Darbuka_faustpower2_f(fConst1);
		fConst3 = 2.0f * (1.0f - 1.0f / fConst2);
		float fConst4 = 1.0f / fConst1;
		fConst5 = (fConst4 + -1.4142135f) / fConst1 + 1.0f;
		float fConst6 = (fConst4 + 1.4142135f) / fConst1 + 1.0f;
		fConst7 = 1.0f / fConst6;
		fConst8 = std::max<float>(1.0f, 0.0005f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 1.0f / std::max<float>(1.0f, 0.02f * fConst0);
		fConst11 = 1.0f / (fConst2 * fConst6);
		fConst12 = 5.7491145f / fConst0;
		fConst13 = 3.1415927f / fConst0;
		fConst14 = std::max<float>(1.0f, 0.0008f * fConst0);
		fConst15 = 1.0f / fConst14;
		fConst16 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst17 = 1.0f / fConst16;
		fConst18 = 7.257079f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.6f);
		fHslider1 = FAUSTFLOAT(1.1e+02f);
		fHslider2 = FAUSTFLOAT(0.35f);
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
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec6[l7] = 0.0f;
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
	
	virtual Darbuka* clone() {
		return new Darbuka();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("darbuka");
		ui_interface->addHorizontalSlider("freq", &fHslider1, FAUSTFLOAT(1.1e+02f), FAUSTFLOAT(5e+01f), FAUSTFLOAT(1.2e+03f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("ring", &fHslider2, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("snap", &fHslider0, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = float(fHslider0);
		float fSlow2 = fConst11 * (0.7f * fSlow1 + 0.5f);
		float fSlow3 = float(fHslider1);
		float fSlow4 = std::max<float>(3e+02f, 2.4f * fSlow3);
		float fSlow5 = std::tan(fConst12 * fSlow4);
		float fSlow6 = 2.0f * (1.0f - 1.0f / Darbuka_faustpower2_f(fSlow5));
		float fSlow7 = 1.0f / fSlow5;
		float fSlow8 = (fSlow7 + -0.029411765f) / fSlow5 + 1.0f;
		float fSlow9 = (fSlow7 + 0.029411765f) / fSlow5 + 1.0f;
		float fSlow10 = 1.0f / fSlow9;
		float fSlow11 = 0.5f / (fSlow5 * fSlow9);
		float fSlow12 = std::tan(fConst13 * fSlow4);
		float fSlow13 = 2.0f * (1.0f - 1.0f / Darbuka_faustpower2_f(fSlow12));
		float fSlow14 = 1.0f / fSlow12;
		float fSlow15 = (fSlow14 + -0.033333335f) / fSlow12 + 1.0f;
		float fSlow16 = (fSlow14 + 0.033333335f) / fSlow12 + 1.0f;
		float fSlow17 = 1.0f / fSlow16;
		float fSlow18 = 0.8f / (fSlow12 * fSlow16);
		float fSlow19 = 1.0f / std::max<float>(1.0f, fConst0 * (0.04f * fSlow1 + 0.05f));
		float fSlow20 = 0.85f * std::max<float>(0.0f, std::min<float>(1.0f, 0.00625f * (fSlow3 + -1.4e+02f)));
		float fSlow21 = 1.9f * (fSlow20 + 0.15f);
		float fSlow22 = 1.0f / std::max<float>(1.0f, fConst0 * (0.25f * float(fHslider2) + 0.18f));
		float fSlow23 = std::max<float>(7e+01f, std::min<float>(fSlow3, 1.6e+02f));
		float fSlow24 = std::tan(fConst18 * fSlow23);
		float fSlow25 = 2.0f * (1.0f - 1.0f / Darbuka_faustpower2_f(fSlow24));
		float fSlow26 = 1.0f / fSlow24;
		float fSlow27 = (fSlow26 + -0.05f) / fSlow24 + 1.0f;
		float fSlow28 = (fSlow26 + 0.05f) / fSlow24 + 1.0f;
		float fSlow29 = 1.0f / fSlow28;
		float fSlow30 = 0.3f / (fSlow24 * fSlow28);
		float fSlow31 = std::tan(fConst13 * fSlow23);
		float fSlow32 = 2.0f * (1.0f - 1.0f / Darbuka_faustpower2_f(fSlow31));
		float fSlow33 = 1.0f / fSlow31;
		float fSlow34 = (fSlow33 + -0.071428575f) / fSlow31 + 1.0f;
		float fSlow35 = (fSlow33 + 0.071428575f) / fSlow31 + 1.0f;
		float fSlow36 = 1.0f / fSlow35;
		float fSlow37 = 1.0f / (fSlow31 * fSlow35);
		float fSlow38 = 3.4f * (1.0f - fSlow20);
		float fSlow39 = 0.32f * float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iRec1[0] = (iRec1[1] + (iRec1[1] > 0)) * (fSlow0 <= fVec0[1]) + (fSlow0 > fVec0[1]);
			float fTemp0 = float(iRec1[0]);
			iRec2[0] = 1103515245 * iRec2[1] + 12345;
			fRec0[0] = 4.656613e-10f * float(iRec2[0]) * std::max<float>(0.0f, std::min<float>(fConst9 * fTemp0, fConst10 * (fConst8 - fTemp0) + 1.0f)) - fConst7 * (fConst5 * fRec0[2] + fConst3 * fRec0[1]);
			float fTemp1 = fSlow0 - fVec0[1];
			float fTemp2 = fTemp1 * float(fTemp1 > 0.0f);
			fRec3[0] = fTemp2 - fSlow10 * (fSlow8 * fRec3[2] + fSlow6 * fRec3[1]);
			fRec4[0] = fTemp2 - fSlow17 * (fSlow15 * fRec4[2] + fSlow13 * fRec4[1]);
			fRec5[0] = fTemp2 - fSlow29 * (fSlow27 * fRec5[2] + fSlow25 * fRec5[1]);
			fRec6[0] = fTemp2 - fSlow36 * (fSlow34 * fRec6[2] + fSlow32 * fRec6[1]);
			float fTemp3 = fSlow39 * (fSlow38 * (fSlow37 * (fRec6[0] - fRec6[2]) + fSlow30 * (fRec5[0] - fRec5[2])) * std::max<float>(0.0f, std::min<float>(fConst17 * fTemp0, fSlow22 * (fConst16 - fTemp0) + 1.0f)) + fSlow21 * std::max<float>(0.0f, std::min<float>(fConst15 * fTemp0, fSlow19 * (fConst14 - fTemp0) + 1.0f)) * (fSlow18 * (fRec4[0] - fRec4[2]) + fSlow11 * (fRec3[0] - fRec3[2]) + fSlow2 * (fRec0[0] + fRec0[2] - 2.0f * fRec0[1])));
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
			fRec6[2] = fRec6[1];
			fRec6[1] = fRec6[0];
		}
	}

};

#endif
