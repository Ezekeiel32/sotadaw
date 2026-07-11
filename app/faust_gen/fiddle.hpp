/* ------------------------------------------------------------
name: "fiddle"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Fiddle -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Fiddle_H__
#define  __Fiddle_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Fiddle
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

class FiddleSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec7[2];
	
  public:
	
	int getNumInputsFiddleSIG0() {
		return 0;
	}
	int getNumOutputsFiddleSIG0() {
		return 1;
	}
	
	void instanceInitFiddleSIG0(int sample_rate) {
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iVec2[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec7[l6] = 0;
		}
	}
	
	void fillFiddleSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec7[0] = (iVec2[1] + iRec7[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec7[0]));
			iVec2[1] = iVec2[0];
			iRec7[1] = iRec7[0];
		}
	}

};

static FiddleSIG0* newFiddleSIG0() { return (FiddleSIG0*)new FiddleSIG0(); }
static void deleteFiddleSIG0(FiddleSIG0* dsp) { delete dsp; }

static float Fiddle_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0FiddleSIG0[65536];

class Fiddle : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst5;
	float fConst7;
	float fConst9;
	float fConst11;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec2[2];
	float fConst12;
	float fRec3[2];
	FAUSTFLOAT fHslider0;
	float fConst13;
	int iRec4[2];
	float fConst14;
	float fConst15;
	FAUSTFLOAT fHslider1;
	float fConst16;
	float fRec8[2];
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	float fRec5[2];
	float fRec1[3];
	float fConst17;
	float fConst19;
	float fConst21;
	float fConst23;
	float fRec9[3];
	float fConst24;
	float fConst26;
	float fConst28;
	float fConst30;
	float fRec10[3];
	float fConst31;
	FAUSTFLOAT fHslider4;
	FAUSTFLOAT fHslider5;
	float fRec0[3];
	
 public:
	Fiddle() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Fiddle -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/asr:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "fiddle.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "fiddle");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
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
		FiddleSIG0* sig0 = newFiddleSIG0();
		sig0->instanceInitFiddleSIG0(sample_rate);
		sig0->fillFiddleSIG0(65536, ftbl0FiddleSIG0);
		deleteFiddleSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(21991.148f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / Fiddle_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.4142135f) / fConst1 + 1.0f;
		fConst5 = 1.0f / ((fConst3 + 1.4142135f) / fConst1 + 1.0f);
		float fConst6 = std::tan(3455.752f / fConst0);
		fConst7 = 2.0f * (1.0f - 1.0f / Fiddle_faustpower2_f(fConst6));
		float fConst8 = 1.0f / fConst6;
		fConst9 = (fConst8 + -0.33333334f) / fConst6 + 1.0f;
		float fConst10 = (fConst8 + 0.33333334f) / fConst6 + 1.0f;
		fConst11 = 1.0f / fConst10;
		fConst12 = 1.0f / std::max<float>(1.0f, 0.15f * fConst0);
		fConst13 = 0.15f / std::max<float>(1.0f, 0.08f * fConst0);
		fConst14 = 1.0f / std::max<float>(1.0f, 0.1f * fConst0);
		fConst15 = 1.0f / std::max<float>(1.0f, 0.35f * fConst0);
		fConst16 = 1.0f / fConst0;
		fConst17 = 0.5f / (fConst6 * fConst10);
		float fConst18 = std::tan(1476.5486f / fConst0);
		fConst19 = 2.0f * (1.0f - 1.0f / Fiddle_faustpower2_f(fConst18));
		float fConst20 = 1.0f / fConst18;
		fConst21 = (fConst20 + -0.25f) / fConst18 + 1.0f;
		float fConst22 = (fConst20 + 0.25f) / fConst18 + 1.0f;
		fConst23 = 1.0f / fConst22;
		fConst24 = 0.7f / (fConst18 * fConst22);
		float fConst25 = std::tan(895.3539f / fConst0);
		fConst26 = 2.0f * (1.0f - 1.0f / Fiddle_faustpower2_f(fConst25));
		float fConst27 = 1.0f / fConst25;
		fConst28 = (fConst27 + -0.25f) / fConst25 + 1.0f;
		float fConst29 = (fConst27 + 0.25f) / fConst25 + 1.0f;
		fConst30 = 1.0f / fConst29;
		fConst31 = 0.8f / (fConst25 * fConst29);
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.05f);
		fHslider1 = FAUSTFLOAT(5.5f);
		fHslider2 = FAUSTFLOAT(0.007f);
		fHslider3 = FAUSTFLOAT(4.4e+02f);
		fHslider4 = FAUSTFLOAT(0.55f);
		fHslider5 = FAUSTFLOAT(0.5f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec2[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec3[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec4[l4] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec8[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec5[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec1[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec9[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec10[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec0[l12] = 0.0f;
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
	
	virtual Fiddle* clone() {
		return new Fiddle();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fiddle");
		ui_interface->addHorizontalSlider("bow", &fHslider0, FAUSTFLOAT(0.05f), FAUSTFLOAT(0.005f), FAUSTFLOAT(0.3f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("bright", &fHslider4, FAUSTFLOAT(0.55f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider3, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(1e+02f), FAUSTFLOAT(2.5e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("vibrate", &fHslider1, FAUSTFLOAT(5.5f), FAUSTFLOAT(3.0f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("vibrato", &fHslider2, FAUSTFLOAT(0.007f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.02f), FAUSTFLOAT(0.0005f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = 1.0f / fSlow2;
		float fSlow4 = fConst16 * float(fHslider1);
		float fSlow5 = float(fHslider2);
		float fSlow6 = float(fHslider3);
		float fSlow7 = float(fHslider4);
		float fSlow8 = 1.0f - 0.5f * fSlow7;
		float fSlow9 = 0.28f * float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec2[0] = iSlow1 * (iRec2[1] + 1);
			float fTemp0 = float(iRec2[0]);
			fRec3[0] = fSlow0 + fRec3[1] * float(fVec1[1] >= fSlow0);
			iRec4[0] = 1103515245 * iRec4[1] + 12345;
			float fTemp1 = ((1 - iVec0[1]) ? 0.0f : fSlow4 + fRec8[1]);
			fRec8[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = std::max<float>(1.1920929e-07f, std::fabs(fSlow6 * (fSlow5 * ftbl0FiddleSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst15 * fRec3[0], 1.0f) - fConst14 * fTemp0) + 1.0f)));
			float fTemp3 = fRec5[1] + fConst16 * fTemp2;
			float fTemp4 = fTemp3 + -1.0f;
			int iTemp5 = fTemp4 < 0.0f;
			fRec5[0] = ((iTemp5) ? fTemp3 : fTemp4);
			float fRec6 = ((iTemp5) ? fTemp3 : fTemp3 + fTemp4 * (1.0f - fConst0 / fTemp2));
			float fTemp6 = (2.0f * fRec6 + 1.8626451e-11f * float(iRec4[0]) + -1.0f) * std::max<float>(0.0f, std::min<float>(fSlow3 * fRec3[0], std::max<float>(fConst13 * (fSlow2 - fRec3[0]) + 1.0f, 0.85f)) * (1.0f - fConst12 * fTemp0));
			fRec1[0] = fTemp6 - fConst11 * (fConst9 * fRec1[2] + fConst7 * fRec1[1]);
			fRec9[0] = fTemp6 - fConst23 * (fConst21 * fRec9[2] + fConst19 * fRec9[1]);
			fRec10[0] = fTemp6 - fConst30 * (fConst28 * fRec10[2] + fConst26 * fRec10[1]);
			fRec0[0] = fSlow9 * (fSlow7 * fTemp6 + fSlow8 * (fConst31 * (fRec10[0] - fRec10[2]) + fConst24 * (fRec9[0] - fRec9[2]) + fConst17 * (fRec1[0] - fRec1[2]))) - fConst5 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp7 = fConst5 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp7);
			output1[i0] = FAUSTFLOAT(fTemp7);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			fRec3[1] = fRec3[0];
			iRec4[1] = iRec4[0];
			fRec8[1] = fRec8[0];
			fRec5[1] = fRec5[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec9[2] = fRec9[1];
			fRec9[1] = fRec9[0];
			fRec10[2] = fRec10[1];
			fRec10[1] = fRec10[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
